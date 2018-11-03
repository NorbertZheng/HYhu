#from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template import loader

def send_confirm_email(subject, template_path, info, _from, to):
	html_content = loader.render_to_string(
		template_path,
		{
			'name': info['name'],
			'url': info['url'],
			'img': info['img'],
		}
	)
	print(html_content)
	msg = EmailMessage(subject, html_content, _from, to)
	msg.content_subtype = "html" 				# Main content is now text/html
	msg.send()