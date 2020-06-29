
# runner

## Non-Python dependencies

* strace

* gcc

* python3-develop

  

## Usful links that i used

*  [pdb Docs page ](<https://docs.python.org/3/library/pdb.html>)

*  [Argparse Docs page](https://docs.python.org/3.6/library/argparse.html)

*  [Psutil Docs page](https://psutil.readthedocs.io/en/latest/)

*  [Logging Docs page](https://docs.python.org/2.6/library/logging.html)

*  [SubProcess Docs page](https://docs.python.org/3/library/subprocess.html)

*  [PEP8 Docs page](https://www.python.org/dev/peps/pep-0008/)

*  [Threading toturial](https://www.datacamp.com/community/tutorials/threading-in-python?utm_source=adwords_ppc&utm_campaignid=9942305733&utm_adgroupid=100189364546&utm_device=c&utm_keyword=&utm_matchtype=b&utm_network=g&utm_adpostion=&utm_creative=332602034343&utm_targetid=aud-299261629574:dsa-929501846124&utm_loc_interest_ms=&utm_loc_physical_ms=1007981&gclid=Cj0KCQjw3Nv3BRC8ARIsAPh8hgKGLhBKrj1Q71EZ8VjlKjcfUZS0i_Ark4VgOFdLWozZePsXmBOFPPkaAoD2EALw_wcB)

* [PyTest  tutorial]([https://www.guru99.com/pytest-tutorial.html](https://www.guru99.com/pytest-tutorial.html))
* [Capture Ctrl+C]([https://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python](https://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python))
  
## Challenges I have experienced throughout the task
*  The first challenge that I faced resulted from using the Multiprocessing module instead of the Threading module for concurrency. When I used the Multiprocessing module each job that the script created was running in a different process and therefore if used exit from one process the other processes proceeded to run, This made it difficult for the error handling. It also affected the handle of the CTR+C and made it print the summary twice. When I changed my code to run with the Threading module for concurrency, all of the error handling problems that the first module caused, were fixed, when you use Threading all the jobs run under one process. When all the jobs are running under one process they can share variables (when you set them as global) and when one job fails, it can be easier to stop other jobs.
*  The second one was handling commands that contain special characters like: 
*   ;
*   |
*   $
The Subprocess command ignores these symbols and use the characters that come after these symbols as an extra args. A thing that makes the command fail. To handle this problem Subprocess as an option to add: `shell=True`, but according to the docs when using this option the PID of the command is the PID of the shell and not of the command. In order to solve it, I tried to use this option on several commands and I understood that only when using special symbols the PID of the command it the PID of the shell. My solution was when the PID of the command was the PID of the shell I took the first PID from the child processes of the shell.