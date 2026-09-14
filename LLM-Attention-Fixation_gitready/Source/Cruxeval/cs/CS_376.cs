using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        for (int i = 0; i < text.Length; i++)
        {
            if (text.Substring(0, i).StartsWith("two"))
            {
                return text.Substring(i);
            }
        }
        return "no";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("2two programmers")).Equals(("no")));
    }

}
