using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Drawing.Imaging;
using System.Drawing;
using System.Windows.Forms;

namespace ClipCloud
{
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length == 0) {
                Console.WriteLine("No parameters specfied");                    
                return;
            }
            //Console.WriteLine(args);
            switch (args[0])
            {
                case "screenshot":
                    ScreenShot s = new ScreenShot();
                    string folder = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
                    folder += "\\ClipCloud\\img"
                    string path = s.TakeScreenshot(folder);
                    Console.WriteLine(path);
                    break;
                case "foo":
                    break;
            }
            //Console.ReadLine();
        }
    }

    class ScreenShot
    {
        /// <summary>
        /// Captures the current pixel data of the users screen and saves it to a png file.
        /// </summary>
        /// <returns>A string denoting the path of the saved image file.</returns>
        public string TakeScreenshot(string screenshotSaveDir)
        {
            //Create a directory to store all screenshots the user takes,
            //if one hasn't been made already
            if (!Directory.Exists(screenshotSaveDir))
            {
                DirectoryInfo dri = Directory.CreateDirectory(screenshotSaveDir);
            }

            Bitmap screenshot;
            Graphics screenshotGraphic;
            int width = 1;
            int height = 1;
            int x = 0;
            int y = 0;

            if(width != 0){
                width = Screen.PrimaryScreen.Bounds.Width;
            }
            
            if(height != 0){
                height = Screen.PrimaryScreen.Bounds.Height;
            }

            screenshot = new Bitmap(width, height, PixelFormat.Format32bppArgb);
            screenshotGraphic = Graphics.FromImage(screenshot);

            //Copy the specified rectangle of pixels to a temporary object
            //Copy the whole screen
            screenshotGraphic.CopyFromScreen(x, y, 0, 0, Screen.PrimaryScreen.Bounds.Size, CopyPixelOperation.SourceCopy);

            //Only copy the current window
            //gfxScrn.CopyFromScreen(this.Bounds.X, this.Bounds.Y, 0, 0, this.Bounds.Size, CopyPixelOperation.SourceCopy);

            //Save the image with a unique file name based on the current time
            string time = DateTime.Now.ToString().Replace("/", "").Replace(":", "");
            string fileName = "screenshot-" + time + ".png";
            string imagePath = screenshotSaveDir + "\\" + fileName;
            screenshot.Save(imagePath, ImageFormat.Png);

            return fileName;
        }
    }
}
