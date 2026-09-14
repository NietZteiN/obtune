using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Program
{
    static string F(string text, string characters)
    {
        foreach (char c in characters)
        {
            text = text.TrimEnd(c);
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("r;r;r;r;r;r;r;r;r"), ("x.r")).Equals(("r;r;r;r;r;r;r;r;")));
    }

}
