using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string text) {
        int length = text.Length;
        int half = length / 2;
        byte[] encode = Encoding.ASCII.GetBytes(text.Substring(0, half));
        if (text.Substring(half) == Encoding.ASCII.GetString(encode))
        {
            return true;
        }
        else
        {
            return false;
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("bbbbr")) == (false));
    }

}
