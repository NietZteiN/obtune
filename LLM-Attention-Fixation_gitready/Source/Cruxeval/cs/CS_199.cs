using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Program
{
    static string F(string s, string character)
    {
        int count = s.Count(c => c == character[0]);
        string baseStr = new string(character[0], count + 1);
        return s.EndsWith(baseStr) ? s.Substring(0, s.Length - baseStr.Length) : s;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("mnmnj krupa...##!@#!@#$$@##"), ("@")).Equals(("mnmnj krupa...##!@#!@#$$@##")));
    }

}
