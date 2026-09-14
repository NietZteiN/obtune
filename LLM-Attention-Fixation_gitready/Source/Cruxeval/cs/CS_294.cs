using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string n, string m, string text) {
        if (text.Trim() == "")
        {
            return text;
        }

        char head = text[0];
        string mid = text.Substring(1, text.Length - 2);
        char tail = text[text.Length - 1];

        string joined = head.ToString().Replace(n, m) + mid.Replace(n, m) + tail.ToString().Replace(n, m);
        return joined;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("x"), ("$"), ("2xz&5H3*1a@#a*1hris")).Equals(("2$z&5H3*1a@#a*1hris")));
    }

}
