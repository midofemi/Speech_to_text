import os
class S3Sync:
    """
    This class is use for syncing things back and forth from AWS to our machine or vice versa. So it will take the folder from our machine 
    and sync it to S3 bucket. We can do the same if we want. Meaning If we have a folder or files or both from AWS. We can sync those
    files or folders to our local machine. Thanks to AWS CLI configuration. All you'll need is some commands which you can use on your
    terminal or you can ask chatGPT to show you those commands or ask google
    """

    def sync_folder_to_s3(self,folder,aws_bucket_url):
        command = f"aws s3 sync {folder} {aws_bucket_url} "
        os.system(command)

    def sync_folder_from_s3(self,folder,aws_bucket_url):
        command = f"aws s3 sync  {aws_bucket_url} {folder} "
        os.system(command)