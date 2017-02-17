# t-hoarder_kit
Set of basic tools to extract data from the Twitter API and visualize graphs

T-hoarder_kit.sh provides a menu for access to python scripts. The scripts directory path must be included in the environment variable $PATH.

Assume that the access keys are in the keys directory and the results are deposited in the store/experiment directory

     T-hoarder --+-- keys
                 |
                 +- scripts
                 |
                 +- store -+-- experiment-1
                           |
                           +-- experiment-2
                         ....
                           |
                           +-- experiment-n
                 

Using the python scripts from the command line the keys and the results is free to place them where you want

      tweet_auth.py [-h] keys_app user

      tweet_rest.py [-h] [--id_user] [--fast]
                     (--profile | --followers | --following | --relations | --conections | --tweets)
                     keys_app keys_user file_users

      tweet_rest.py [-h] [--id_user] [--fast]
                     (--profile | --followers | --following | --relations | --conections | --tweets)
                     keys_app keys_user file_users
 
      tweet_streaming.py [-h] [--users USERS] [--words WORDS]
                          [--locations LOCATIONS]
                          app_keys user_keys dir_out file_dest

      tweets_grafo.py [-h] [--top_size TOP_SIZE] (--RT | --mention | --reply)
                       file_in


For more information, visit the wiki
