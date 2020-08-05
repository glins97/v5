import traceback
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "v5.settings")
django.setup()

import logging
logger = logging.getLogger('django')

from django.utils.timezone import now
from tps.models import TPS, TPSAnswer, Question, QuestionAnswer
from tps.auxiliary import separate_students

def get_question_html(question, question_answer):
    answer = ''
    if question_answer:
        answer = question_answer.answer
    return f"""
            <tr style="height:21px">
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);text-align:right;border:1px solid rgb(204,204,204)">{question.number}</td>
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;{'background-color:rgb(182,215,168)' if question.correct_answer == 'A' else ''};border:1px solid rgb(204,204,204)">{'X' if answer == 'A' else '<br>'}</td>
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;{'background-color:rgb(182,215,168)' if question.correct_answer == 'B' else ''};border:1px solid rgb(204,204,204)">{'X' if answer == 'B' else '<br>'}</td>
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;{'background-color:rgb(182,215,168)' if question.correct_answer == 'C' else ''};border:1px solid rgb(204,204,204)">{'X' if answer == 'C' else '<br>'}</td>
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;{'background-color:rgb(182,215,168)' if question.correct_answer == 'D' else ''};border:1px solid rgb(204,204,204)">{'X' if answer == 'D' else '<br>'}</td>
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;{'background-color:rgb(182,215,168)' if question.correct_answer == 'E' else ''};border:1px solid rgb(204,204,204)">{'X' if answer == 'E' else '<br>'}</td>
            </tr> 
            """

def get_group(tpses, id):
    for tps in tpses:
        for grade_group in tpses[tps]:
            if id in tpses[tps][grade_group]:
                return grade_group
    return ''

def get_rank(tpses, id):
    rank = 0
    for tps in tpses:
        for grade_group in ['SCORE_Z', 'TBL', 'CBT']:
            if grade_group not in tpses[tps]: continue
            for aid in tpses[tps][grade_group]:
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
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(67,67,67);color:rgb(255,255,255);text-align:center;border:1px solid rgb(204,204,204)" rowspan="1" colspan="6">Cartão de respostas</td>
                            </tr>
                            <tr style="height:21px">
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">Questão</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">A</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">B</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">C</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">D</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">E</td>
                            </tr>
                            {questions_rows}
                        </tbody>
                    </table>
                </span>
                """
            mail_body = f'<p>Aluno: {tps_answer.name}</p>'   
            mail_body += f'<p>Nota: {tps_answer.grade}</p>' 
            tps_answer.rank = get_rank(tpses, tps_answer.id)
            tps_answer.grade_group = get_group(tpses, tps_answer.id)
            tps_answer.save()

            if tps_answer.tps.notify:
                mail_body += f'<p>Ranking: {tps_answer.rank}</p>'   
                mail_body += f'<p>Grupo: {tps_answer.grade_group}</p>'   

            if tps_answer.tps.solutions:
                mail_body += f'<p>As soluções comentadas se encotram em anexo (ou, caso não, acesse <a href="https://ppa.digital/{tps_answer.tps.solutions}"> este link</a> pelo computador).</p>'    

            mail_body += f'<p>Seu cartão de respostas se encontra abaixo. Células marcadas com um \'X\' indicam suas respostas. Células em verde, o gabarito oficial.<br><p>{table}'
            if send_mail(tps_answer.email, f'respostas {tps_answer.tps}', mail_body, str(tps_answer.tps.solutions.file) if tps_answer.tps.solutions else ''):
                tps_answer.mailed = True
                tps_answer.mailed_answers = True
                tps_answer.save()
        except Exception as e:
            logger.error(f'Error mailing TPS Answer {tps_answer}. Error {e}', exc_info=e)
    logger.info(f'General tps results delivery finished')

def _mail_answers_jua():
    answers = TPSAnswer.objects.filter(mailed_results=False, tps__end_date__lte=now(), tps__campus='JUA')
    tpses = {
        tps: separate_students(tps) for tps in list(set([answer.tps for answer in answers]))
    } 
    for tps in tpses:
        for grade_group in tpses[tps]:
            tpses[tps][grade_group] = tpses[tps][grade_group]['xE'].tolist() # get only ids 

    if not answers.count(): return
    logger.info('Starting general tps results delivery')
    for tps_answer in answers:
        logger.info(f'Mailing TPS Answer JUA {tps_answer}')
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
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(67,67,67);color:rgb(255,255,255);text-align:center;border:1px solid rgb(204,204,204)" rowspan="1" colspan="6">Cartão de respostas</td>
                            </tr>
                            <tr style="height:21px">
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">Questão</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">A</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">B</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">C</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">D</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">E</td>
                            </tr>
                            {questions_rows}
                        </tbody>
                    </table>
                </span>
                """
            mail_body = f'<p>Aluno: {tps_answer.name}</p>'   
            mail_body += f'<p>Nota: {tps_answer.grade}</p>' 
            tps_answer.rank = get_rank(tpses, tps_answer.id)
            tps_answer.grade_group = get_group(tpses, tps_answer.id)
            tps_answer.save()

            if tps_answer.tps.notify:
                mail_body += f'<p>Ranking: {tps_answer.rank}</p>'   
                mail_body += f'<p>Grupo: {tps_answer.grade_group}</p>'   

            if tps_answer.tps.solutions:
                mail_body += f'<p>As soluções comentadas se encotram em anexo (ou, caso não, acesse <a href="https://ppa.digital/{tps_answer.tps.solutions}"> este link</a> pelo computador).</p>'    

            mail_body += f'<p>Seu cartão de respostas se encontra abaixo. Células marcadas com um \'X\' indicam suas respostas. Células em verde, o gabarito oficial.<br><p>{table}'
            if send_mail(tps_answer.email, f'resultados {tps_answer.tps}', mail_body, str(tps_answer.tps.solutions.file) if tps_answer.tps.solutions else ''):
                tps_answer.mailed_results = True
                tps_answer.mailed_answers = True
                tps_answer.save()
        except Exception as e:
            logger.error(f'Error mailing TPS Answer {tps_answer}. Error {e}', exc_info=e)
    logger.info(f'General tps results delivery finished')

def _mail_results_bsb():
    answers = TPSAnswer.objects.filter(mailed_results=False, tps__end_date__lte=now(), tps__campus='BSB')
    tpses = {
        tps: separate_students(tps) for tps in list(set([answer.tps for answer in answers]))
    } 
    for tps in tpses:
        for grade_group in tpses[tps]:
            tpses[tps][grade_group] = tpses[tps][grade_group]['xE'].tolist() # get only ids 

    if not answers.count(): return
    logger.info('Starting general tps results delivery')
    for tps_answer in answers:
        logger.info(f'Mailing TPS Answer BSB {tps_answer}')
        try:
            mail_body = f'<p>Aluno: {tps_answer.name}</p>'   
            mail_body += f'<p>Nota: {tps_answer.grade}</p>' 
            tps_answer.rank = get_rank(tpses, tps_answer.id)
            tps_answer.grade_group = get_group(tpses, tps_answer.id)
            tps_answer.save()

            if tps_answer.tps.notify:
                mail_body += f'<p>Ranking: {tps_answer.rank}</p>'   
                mail_body += f'<p>Grupo: {tps_answer.grade_group}</p>'   

            mail_body += f'<p>As soluções comentadas (e seu caderno de respostas) serão enviadas por e-mail às 18:00!</p>'    
            if send_mail(tps_answer.email, f'respostas {tps_answer.tps}', mail_body):
                tps_answer.mailed_results = True
                tps_answer.save()
        except Exception as e:
            logger.error(f'Error mailing TPS Answer {tps_answer}. Error {e}', exc_info=e)
    logger.info(f'General tps results delivery finished')

def _mail_answers_bsb():
    if (now().hour != 18): return

    answers = TPSAnswer.objects.filter(mailed_answers=False, tps__end_date__lte=now(), tps__campus='BSB')
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
            logger.info(f'Mailing TPS Answer Results BSB {tps_answer}')
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
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(67,67,67);color:rgb(255,255,255);text-align:center;border:1px solid rgb(204,204,204)" rowspan="1" colspan="6">Cartão de respostas</td>
                            </tr>
                            <tr style="height:21px">
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">Questão</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">A</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">B</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">C</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">D</td>
                                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);border:1px solid rgb(204,204,204)">E</td>
                            </tr>
                            {questions_rows}
                        </tbody>
                    </table>
                </span>
                """
            mail_body = ''
            if tps_answer.tps.solutions:
                mail_body += f'<p>As soluções comentadas se encotram em anexo (ou, caso não, acesse <a href="https://ppa.digital/{tps_answer.tps.solutions}"> este link</a> pelo computador).</p>'    

            mail_body += f'<p>Seu cartão de respostas se encontra abaixo. Células marcadas com um \'X\' indicam suas respostas. Células em verde, o gabarito oficial.<br><p>{table}'
            if send_mail(tps_answer.email, f'respostas {tps_answer.tps}', mail_body):
                tps_answer.mailed_answers = True
                tps_answer.save()
        except Exception as e:
            logger.error(f'Error mailing TPS Answer {tps_answer}. Error {e}', exc_info=e)
    logger.info(f'General tps results delivery finished')

def main():
    _mail_answers_bsb()
    _mail_results_bsb()
    _mail_answers_goi()
    _mail_answers_jua()
            
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.encoders import encode_base64
import codecs
from threading import _start_new_thread

def send_mail(email, subject, message, attachment=''):
    msg = MIMEMultipart()
    password = 'campusppa'
    msg['To'] = 'nombregag@gmail.com'
    msg['From'] = 'adm.ppa.digital@gmail.com'
    msg['Subject'] = 'PPA Digital: ' + subject
    if attachment:
        openedfile = None
        with open(attachment, 'rb') as opened:
            openedfile = opened.read()
        attachedfile = MIMEApplication(openedfile, _subtype = "pdf", _encoder=encode_base64)
        attachedfile.add_header('content-disposition', 'attachment', filename=attachment.split('/')[-1])
        msg.attach(attachedfile)
    msg.attach(MIMEText(message, 'html'))
    with smtplib.SMTP('smtp.gmail.com: 587') as server:
        server.starttls()
        server.login(msg['From'], password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
    return True

if __name__ == '__main__':
    main()
