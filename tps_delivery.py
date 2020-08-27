import traceback
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "v5.settings")
django.setup()

import logging
logger = logging.getLogger('django')

from django.utils.timezone import now
from tps.models import TPS, TPSAnswer, Question, QuestionAnswer, TPSScore
from tps.auxiliary import separate_students, generate_cbt, generate_tbl, generate_score_z, generate_distrator

import subprocess

from mailer.mailer import send_templated_mail

def get_question_html(question, question_answer):
    answer = ''
    if question_answer:
        answer = question_answer.answer
    return f"""
            <tr style="height:21px">
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;color:#555555;text-align:right;border:1px solid #eeeeee">{question.number}</td>
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;{'background-color:#bff8ff' if question.correct_answer == 'A' else ''};border:1px solid #eeeeee">{'X' if answer == 'A' else '<br>'}</td>
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;{'background-color:#bff8ff' if question.correct_answer == 'B' else ''};border:1px solid #eeeeee">{'X' if answer == 'B' else '<br>'}</td>
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;{'background-color:#bff8ff' if question.correct_answer == 'C' else ''};border:1px solid #eeeeee">{'X' if answer == 'C' else '<br>'}</td>
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;{'background-color:#bff8ff' if question.correct_answer == 'D' else ''};border:1px solid #eeeeee">{'X' if answer == 'D' else '<br>'}</td>
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;{'background-color:#bff8ff' if question.correct_answer == 'E' else ''};border:1px solid #eeeeee">{'X' if answer == 'E' else '<br>'}</td>
            </tr> 
            """

def get_group(tps, id):
    for grade_group in tps:
        if id in tps[grade_group]:
            return grade_group
    return ''

def get_rank(tps, id):
    for grade_group in ['SCORE_Z', 'TBL', 'CBT']:
        rank = 0
        if grade_group not in tps: continue
        for aid in tps[grade_group]:
            rank += 1
            if aid == id:
                return rank
    return ''

def _mail_answers_goi():
    answers = TPSAnswer.objects.filter(mailed_results=False, tps__end_date__lte=now(), tps__campus='GOI')
    tpses = {
        tps: separate_students(tps) for tps in list(set([answer.tps for answer in answers]))
    } 
    for tps in tpses:
        for grade_group in tpses[tps]:
            tpses[tps][grade_group] = tpses[tps][grade_group]['xE'].tolist() # get only ids 

    if not answers.count(): return
    logger.info('Starting general tps results delivery')
    for tps_answer in answers:
        logger.info(f'Mailing TPS Answer GOI {tps_answer}')
        try:
            questions = sorted(Question.objects.filter(tps=tps_answer.tps), key=lambda question: question.number)

            questions_rows = ''
            for question in questions:
                questions_rows += get_question_html(question, QuestionAnswer.objects.filter(tps_answer=tps_answer, question=question).first())
            
            table = f"""
                <span>
                    <table dir="ltr" style="table-layout:fixed;font-size:10pt;font-family:Arial;width:0px;border-collapse:collapse;border:medium none" cellspacing="0" cellpadding="0" border="1">
                        <colgroup>
                            <col width="100"><col width="100"><col width="100"><col width="100"><col width="100"><col width="100">
                        </colgroup>
                        <tbody>
                            <tr style="height:21px">
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:#555555;color:rgb(255,255,255);text-align:center;border:1px solid rgb(204,204,204)" rowspan="1" colspan="6">Cartão de respostas</td>
                            </tr>
                            <tr style="height:21px">
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;color:#555555;border:1px solid #eeeeee">Questão</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;color:#555555;border:1px solid #eeeeee">A</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;color:#555555;border:1px solid #eeeeee">B</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;color:#555555;border:1px solid #eeeeee">C</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;color:#555555;border:1px solid #eeeeee">D</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;color:#555555;border:1px solid #eeeeee">E</td>
                            </tr>
                            {questions_rows}
                        </tbody>
                    </table>
                </span>
                """
            mail_body = f'<p>Aluno: {tps_answer.name}</p>'   
            mail_body += f'<p>Nota: {tps_answer.grade}</p>' 
            tps_answer.rank = get_rank(tpses[tps_answer.tps], tps_answer.id)
            if tps.separate:
                tps_answer.grade_group = get_group(tpses[tps_answer.tps], tps_answer.id)
            tps_answer.save()

            if tps_answer.tps.notify:
                mail_body += f'<p>Ranking: {tps_answer.rank}</p>'   
                if tps.separate:
                    if tps_answer.rank == 1 and tps_answer.grade_group == 'TBL':
                        mail_body += f'<p>Parabéns, você é o aluno master!</p>'   

                    mail_body += f'<p>Grupo: {tps_answer.grade_group}</p>'  
                    current_score = TPSScore.objects.filter(email=tps_answer.email, month=tps_answer.submission_date.month, campus=tps_answer.tps.campus).first()
                    if current_score: 
                        mail_body += '<p>Pontuação total neste mês: {}</p>'.format(current_score.score)   

            if tps_answer.tps.solutions:
                mail_body += f'<p>As soluções comentadas se encotram em anexo (ou, caso não, acesse <a href="https://ppa.digital/{tps_answer.tps.solutions}"> este link</a> pelo computador).</p>'    

            mail_body += f'<p>Seu cartão de respostas se encontra abaixo. Células marcadas com um \'X\' indicam suas respostas. Células em azul, o gabarito oficial.<br><p>{table}'
            mail_body += f'<p>Na eventualidade de problemas ou sugestões, responder diretamente esse email. </p>'    
            if send_templated_mail('base.html', tps_answer.email, f'Respostas {tps_answer.tps}', str(tps_answer.tps.solutions.file) if tps_answer.tps.solutions else '', title='Respostas TPS', body=mail_body, footer="Equipe PPA"):
                tps_answer.mailed_results = True
                tps_answer.mailed_answers = True
                tps_answer.save()
        except Exception as e:
            logger.error(f'Error mailing TPS Answer {tps_answer}. Error {e}', exc_info=e)
    logger.info(f'General tps results delivery finished')

def _mail_results(campus):
    answers = TPSAnswer.objects.filter(mailed_results=False, tps__end_date__lte=now(), tps__campus=campus)
    tpses = {
        tps: separate_students(tps) for tps in list(set([answer.tps for answer in answers]))
    } 
    for tps in tpses:
        for grade_group in tpses[tps]:
            tpses[tps][grade_group] = tpses[tps][grade_group]['xE'].tolist() # get only ids 

    if not answers.count(): return
    logger.info('Starting general tps results delivery')
    for tps_answer in answers:
        logger.info(f'Mailing TPS Answer {campus} {tps_answer}')
        try:
            mail_body = f'<p>Aluno: {tps_answer.name}</p>'   
            mail_body += f'<p>Nota: {tps_answer.grade}</p>' 
            tps_answer.rank = get_rank(tpses[tps_answer.tps], tps_answer.id)
            if tps.separate:
                tps_answer.grade_group = get_group(tpses[tps_answer.tps], tps_answer.id)
            tps_answer.save()

            if tps_answer.tps.notify:
                mail_body += f'<p>Ranking: {tps_answer.rank}</p>'   
                if tps.separate:
                    if tps_answer.rank == 1 and tps_answer.grade_group == 'TBL':
                        mail_body += f'<p>Parabéns, você é o aluno master!</p>'   

                    mail_body += f'<p>Grupo: {tps_answer.grade_group}</p>'  
                    if campus == 'BSB' and tps.group != 'PARTICULARES':
                        current_score = TPSScore.objects.filter(email=tps_answer.email, month=tps_answer.submission_date.month, campus=tps_answer.tps.campus).first()
                        if current_score: 
                            mail_body += '<p>Pontuação total neste mês: {}</p>'.format(current_score.score)   

            mail_body += f'<p>As soluções comentadas serão enviadas por e-mail às 18:00!</p>'  
            if send_templated_mail('base.html', tps_answer.email, f'Resultado {tps_answer.tps}', title='Resultado TPS', body=mail_body, footer="Equipe PPA"):
                tps_answer.mailed_results = True
                tps_answer.save()
        except Exception as e:
            logger.error(f'Error mailing TPS Answer {tps_answer}. Error {e}', exc_info=e)
    logger.info(f'General tps results delivery finished')

def _mail_answers(campus):
    if (now().hour < 18): return

    answers = TPSAnswer.objects.filter(mailed_answers=False, tps__end_date__lte=now(), tps__campus=campus)
    tpses = {
        tps: separate_students(tps) for tps in list(set([answer.tps for answer in answers]))
    } 
    for tps in tpses:
        for grade_group in tpses[tps]:
            tpses[tps][grade_group] = tpses[tps][grade_group]['xE'].tolist() # get only ids 

    if not answers.count(): return
    logger.info('Starting general tps results delivery')
    for tps_answer in answers:
        try:
            logger.info(f'Mailing TPS Answer Results {campus} {tps_answer}')
            questions = sorted(Question.objects.filter(tps=tps_answer.tps), key=lambda question: question.number)

            questions_rows = ''
            for question in questions:
                questions_rows += get_question_html(question, QuestionAnswer.objects.filter(tps_answer=tps_answer, question=question).first())
            
            table = f"""
                <span>
                    <table dir="ltr" style="table-layout:fixed;font-size:10pt;font-family:Arial;width:0px;border-collapse:collapse;border:medium none" cellspacing="0" cellpadding="0" border="1">
                        <colgroup>
                            <col width="100"><col width="100"><col width="100"><col width="100"><col width="100"><col width="100">
                        </colgroup>
                        <tbody>
                            <tr style="height:21px">
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:#555555;color:#ffffff;text-align:center;border:1px solid #eeeeee" rowspan="1" colspan="6">Cartão de respostas</td>
                            </tr>
                            <tr style="height:21px">
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;color:#555555;border:1px solid #eeeeee"></td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;color:#555555;border:1px solid #eeeeee">A</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;color:#555555;border:1px solid #eeeeee">B</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;color:#555555;border:1px solid #eeeeee">C</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;color:#555555;border:1px solid #eeeeee">D</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;color:#555555;border:1px solid #eeeeee">E</td>
                            </tr>
                            {questions_rows}
                        </tbody>
                    </table>
                </span>
                """
            mail_body = ''
            if tps_answer.tps.solutions:
                mail_body += f'<p>As soluções comentadas se encotram em anexo (ou, caso não, acesse <a href="https://ppa.digital/{tps_answer.tps.solutions}"> este link</a> pelo computador).</p>'    

            mail_body += f'<p>Seu cartão de respostas se encontra abaixo. Células marcadas com um \'X\' indicam suas respostas. Células em azul, o gabarito oficial.<br><p>{table}'
            mail_body += f'<p>Na eventualidade de problemas ou sugestões, responder diretamente esse email. </p>'    
            if send_templated_mail('base.html', tps_answer.email, f'Respostas {tps_answer.tps}', str(tps_answer.tps.solutions.file) if tps_answer.tps.solutions else '', title='Resultado TPS', body=mail_body, footer="Equipe PPA"):
                tps_answer.mailed_answers = True
                tps_answer.save()
        except Exception as e:
            logger.error(f'Error mailing TPS Answer {tps_answer}. Error {e}', exc_info=e)
    logger.info(f'General tps results delivery finished')

def _mail_teachers():
    tpses = TPS.objects.filter(mailed=False, end_date__lte=now())
    if not tpses.count(): return

    logger.info('Starting general tps results delivery')
    for tps in tpses:
        logger.info(f'Mailing TPS {tps}')
        try:
            tps.mailed = True
            tps.save()
            if not tps.teacher:
                continue
            
            reports = []
            if tps.campus == 'BSB':
                if tps.group == 'PARTICULARES':
                    tbl = generate_tbl(tps)
                    subprocess.call(['libreoffice', '--headless', '--convert-to',  'pdf', tbl, '--outdir', 'tps/outputs/pdfs'])
                    cbt = generate_cbt(tps)
                    subprocess.call(['libreoffice', '--headless', '--convert-to',  'pdf', cbt, '--outdir', 'tps/outputs/pdfs'])
                    reports.append(tbl)
                    reports.append(cbt)
                else:   
                    score_z = generate_score_z(tps)
                    subprocess.call(['libreoffice', '--headless', '--convert-to',  'pdf', score_z, '--outdir', 'tps/outputs/pdfs'])
                    tbl = generate_tbl(tps)
                    subprocess.call(['libreoffice', '--headless', '--convert-to',  'pdf', tbl, '--outdir', 'tps/outputs/pdfs'])
                    cbt = generate_cbt(tps)
                    subprocess.call(['libreoffice', '--headless', '--convert-to',  'pdf', cbt, '--outdir', 'tps/outputs/pdfs'])
                    reports.append(score_z)
                    reports.append(tbl)
                    reports.append(cbt) 
            else:
                score_z = generate_score_z(tps)
                subprocess.call(['libreoffice', '--headless', '--convert-to',  'pdf', score_z, '--outdir', 'tps/outputs/pdfs'])
                tbl = generate_tbl(tps)
                subprocess.call(['libreoffice', '--headless', '--convert-to',  'pdf', tbl, '--outdir', 'tps/outputs/pdfs'])
                reports.append(score_z)
                reports.append(tbl)

            distrator = generate_distrator(tps)
            subprocess.call(['libreoffice', '--headless', '--convert-to',  'pdf', distrator, '--outdir', 'tps/outputs/pdfs'])
            reports.append(distrator)
            if tps.campus == 'BSB':
                reports.append(cbt.replace('xlsx', 'pdf'))
            mail_body = f'<p>Respostas para TPS {tps} concluídas. Relatórios se encontram em anexo (ou, caso não, acesse <a href="https://ppa.digital/admin/tps/tps/"> este link</a>).</p>'    
            mail_body += f'<p>Na eventualidade de problemas, responder diretamente esse email.</p>'    
            if send_templated_mail('base.html', tps.teacher.email, f'relatórios {tps}', mail_body, reports):
                tps.save()
        except Exception as e:
            logger.error(f'Error mailing TPS {tps}. Error {e}', exc_info=e)
    logger.info(f'General tps results delivery finished')

def main():
    _mail_teachers()
    _mail_answers('BSB')
    _mail_results('BSB')
    _mail_answers('JUA')
    _mail_results('JUA')
    _mail_answers_goi()

if __name__ == "__main__":
    main()