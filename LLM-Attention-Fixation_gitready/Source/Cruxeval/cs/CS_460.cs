using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long amount) {
        int length = text.Length;
        string pre_text = "|";
        if (amount >= length) {
            int extra_space = (int)(amount - length);
            pre_text += new string(' ', extra_space / 2);
            return pre_text + text + pre_text;
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("GENERAL NAGOOR"), (5L)).Equals(("GENERAL NAGOOR")));
    }

}
