using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Program
{
    static string F(string text, string character)
    {
        int count = text.Split(new string[] { character + character }, StringSplitOptions.None).Length - 1;
        return text.Substring(count);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("vzzv2sg"), ("z")).Equals(("zzv2sg")));
    }

}
