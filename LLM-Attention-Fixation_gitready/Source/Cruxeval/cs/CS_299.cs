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
        if (!text.EndsWith(character))
        {
            return F(character + text, character);
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("staovk"), ("k")).Equals(("staovk")));
    }

}
