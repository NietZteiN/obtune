using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string str, string code) {
        string t = "";
        try
        {
            byte[] encodedBytes = Encoding.GetEncoding(code).GetBytes(str);
            if (encodedBytes[encodedBytes.Length - 1] == 10) // Check if last byte is '\n'
            {
                Array.Resize(ref encodedBytes, encodedBytes.Length - 1);
            }
            t = Encoding.UTF8.GetString(encodedBytes);
            return t;
        }
        catch
        {
            return t;
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("towaru"), ("UTF-8")).Equals(("towaru")));
    }

}
