using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<string> txt, string alpha) {
        txt.Sort();
        if (txt.IndexOf(alpha) % 2 == 0)
        {
            txt.Reverse();
        }
        return txt;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"8", (string)"9", (string)"7", (string)"4", (string)"3", (string)"2"})), ("9")).SequenceEqual((new List<string>(new string[]{(string)"2", (string)"3", (string)"4", (string)"7", (string)"8", (string)"9"}))));
    }

}
