// some required defintion 
// to use fopen(..) instead of
// fopen_s(..)

#ifdef _WIN32 
#define _CRT_SECURE_NO_DEPRECATE 
#endif
/************** PROBLEMS ****************/
//  No problems apparent
//  
/************** End ***********************/

//void read(int size, 

#include <stdlib.h>
#include <stdio.h>

void readNumOfBytes(FILE *fp, int size, unsigned char *p_buffer);

int main(void)
{

  FILE *fp; // pointer to a file.
  unsigned char *p_buffer;               // an arrary for the stirng format.
  int size = 256;
 
  // open a file for read with a provided path.
    fp = fopen("//dev//random", "r");  
  //fp = fopen("//temp.txt", "r");  
  
  printf("\n\nReading %d bytes from file...\n\n", size); 
  readNumOfBytes(fp, size, p_buffer);
  
  size = 512;

  printf("\n\nReading %d bytes from file...\n\n", size); 
  readNumOfBytes(fp, size, p_buffer);

  size = 1024;

  printf("\n\nReading %d bytes from file...\n\n", size); 
  readNumOfBytes(fp, size, p_buffer);

  size = 4096;

  printf("\n\nReading %d bytes from file...\n\n", size); 
  readNumOfBytes(fp, size, p_buffer);  

    
  fclose(fp);
  
  return 0;
  
}

void readNumOfBytes(FILE *fp, int size, unsigned char *p_buffer)
{
  static int bytesRead = 0;
  int flag = 0;
  int oldSize = 0;
  
  printf("First entering funcall:\nsize = %d\nbytesRead = %d\n", size,bytesRead);
  if (size > 0){
  p_buffer = (unsigned char *)malloc(sizeof(unsigned char)*size);
  
  // check the file exists.
  if (fp == NULL)
    printf("Sorry, file does not exist!\n\n");
  
  else
    {
      fread(p_buffer, 1, size, fp);
      if(feof(fp))  
	{
	  oldSize = size;
	  size = ftell(fp);    // get the size of the file.
	  flag = 1;
	}
      if(flag)
	{
	  if (bytesRead >= size)
	    {
	      size = 0;
	      printf("\nError: File ran out of data!\n");
	    }
	  else
	    {
	      printf("Sorry, there was less than %d bytes of data in the file!\n", oldSize);
	      printf("The size was adjusted accordingly...\n\n");
	      size -= bytesRead;
	    }
	}
      
      for(int i = 0; i < size && i >= 0; i++)
	{
	  // print data read from file
	  // for testing purposes.
	  printf("%02x ", p_buffer[i]);
	  
	  // Format the printout.
	  if (!((i+1)%10))
	    printf("\n");    
	}
      printf("\n\n\n");
      bytesRead += size;
    }
  }
}
