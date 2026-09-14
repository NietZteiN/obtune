using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Program
{
    static int F(string text)
    {
        if (string.IsNullOrWhiteSpace(text.Trim()))
        {
            return text.Trim().Length;
        }
        return 0; // You can return 0 or any other appropriate value here
    }
    public static void Main(string[] args) {
    Debug.Assert(F((" 	 ")) == (0L));
    }

}
