import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "v5.settings")
django.setup()

from django.utils.timezone import now
from tps.models import TPS, TPSAnswer, Question, QuestionAnswer

def get_question_html(question, question_answer):
    return f"""
            <tr style="height:21px">
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;background-color:rgb(183,183,183);color:rgb(255,255,255);text-align:right;border:1px solid rgb(204,204,204)">{question.number}</td>
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;{'background-color:rgb(182,215,168)' if question.correct_answer == 'A' else ''};border:1px solid rgb(204,204,204)">{'X' if question_answer.answer == 'A' else '<br>'}</td>
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;{'background-color:rgb(182,215,168)' if question.correct_answer == 'B' else ''};border:1px solid rgb(204,204,204)">{'X' if question_answer.answer == 'B' else '<br>'}</td>
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;{'background-color:rgb(182,215,168)' if question.correct_answer == 'C' else ''};border:1px solid rgb(204,204,204)">{'X' if question_answer.answer == 'C' else '<br>'}</td>
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;{'background-color:rgb(182,215,168)' if question.correct_answer == 'D' else ''};border:1px solid rgb(204,204,204)">{'X' if question_answer.answer == 'D' else '<br>'}</td>
                <td style="overflow:hidden;padding:2px 3px;vertical-align:bottom;{'background-color:rgb(182,215,168)' if question.correct_answer == 'E' else ''};border:1px solid rgb(204,204,204)">{'X' if question_answer.answer == 'E' else '<br>'}</td>
            </tr> 
            """

def is_tbl(tps_answer):
    sorted_tps_answers = sorted(TPSAnswer.objects.filter(tps=tps_answer.tps), key=lambda answer: (-answer.grade, answer.submission_date))
    
    print(tps_answer.name, tps_answer.grade, sorted_tps_answers.index(tps_answer), 0.8 * len(sorted_tps_answers))
    if tps_answer.tps.campus == 'GOI':
        if sorted_tps_answers.index(tps_answer) <= 0.8 * len(sorted_tps_answers) - 1:
            return False
    elif tps_answer.tps.campus == 'BSB':
        if sorted_tps_answers.index(tps_answer) <= 10:
            return False
    elif tps_answer.tps.campus == 'JUA':
        if sorted_tps_answers.index(tps_answer) <= 20:
            return False
    return True 

def is_score_z(tps_answer):
    sorted_tps_answers = sorted(TPSAnswer.objects.filter(tps=tps_answer.tps), key=lambda answer: (-answer.grade, answer.submission_date))
    
    if tps_answer.tps.campus == 'GOI':
        if sorted_tps_answers.index(tps_answer) > 0.8 * len(sorted_tps_answers) - 1:
            return False
    elif tps_answer.tps.campus == 'BSB':
        if sorted_tps_answers.index(tps_answer) > 10:
            return False
    elif tps_answer.tps.campus == 'JUA':
        if sorted_tps_answers.index(tps_answer) > 20:
            return False
    return True 

def main():
    for tps_answer in TPSAnswer.objects.filter(mailed=False, tps__end_date__gte=now()):
        try:
            questions = sorted(Question.objects.filter(tps=tps_answer.tps), key=lambda question: question.number)

            questions_rows = ''
            for question in questions:
                questions_rows += get_question_html(question, QuestionAnswer.objects.get(tps_answer=tps_answer, question=question))
            
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
            if tps_answer.tps.tbl and is_tbl(tps_answer):
                mail_body += f'<p>Grupo: TBL</p>'   
            if tps_answer.tps.score_z and is_score_z(tps_answer):
                mail_body += f'<p>Grupo: Score Z</p>'   

            mail_body += f'<p>Para conferir as soluções comentadas, clique <a href="https://ppa.digital/{tps_answer.tps.solutions}"> aqui</a>.</p>'    
            mail_body += f'<p>Seu cartão de respostas se encontra abaixo. Células marcadas com um \'X\' indicam suas respostas. Células em verde, o gabarito oficial.<br><p>{table}'
            if send_mail(tps_answer.email, f'Respostas {tps_answer.tps}', mail_body):
                tps_answer.mailed = True
                tps_answer.save()
        except Exception as e:
            send_mail('gabriel.lins97@gmail.com', f'Error @tps_delivery::main', repr(e)):

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.encoders import encode_base64
import codecs
from threading import _start_new_thread
import logging
logger = logging.getLogger('mailer')

def send_mail(email, subject, message):
    try:
        msg = MIMEMultipart()
        password = 'campusppa'
        msg['To'] = email
        msg['From'] = 'adm.ppa.digital@gmail.com'
        msg['Subject'] = 'PPA Digital: ' + subject

        msg.attach(MIMEText(message, 'html'))
        with smtplib.SMTP('smtp.gmail.com: 587') as server:
            server.starttls()
            server.login(msg['From'], password)
            server.sendmail(msg['From'], msg['To'], msg.as_string())
        return True
    except Exception as e:
        logger.error('exception @send_mail ->', e)
        return False

if __name__ == '__main__':
    main()
