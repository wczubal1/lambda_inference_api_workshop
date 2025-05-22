import paramiko
#Define the instance details                                                                                                                       
instance_id = "9b00025ddaa94914824743ac3fd29f11" 
username = "ubuntu" 
private_key = "C:\Users\witol\Desktop\LambdaSSHkey.txt"  
#Establish an SSH connection to the instance                                                                                                                                                                                   │
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=instance_id, username=username, pkey=private_key)      
#Run the command to execute the model                                                                                                                                                               │
stdin, stdout, stderr = ssh.exec_command('python -c "import torch; from transformers import AutoModelForCausalLM, AutoTokenizer; model_name = \
\'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B\'; model = AutoModelForCausalLM.from_pretrained(model_name); tokenizer = AutoTokenizer.from_pretrained(model_name); \
input_text = \'This is an example sentence.\'; inputs = tokenizer(input_text, return_tensors=\'pt\'); outputs = model.generate(**inputs); print(outputs)"')
#Print the output                                                                                                                                                               │
print(stdout.read().decode())    
#Close the SSH connection                                                                                                                                                                                                                                                                                                 │
ssh.close()  