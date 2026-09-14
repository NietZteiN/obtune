using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        char[] ls = text.ToCharArray();
        Array.Reverse(ls);
        StringBuilder text2 = new StringBuilder();

        for (int i = ls.Length - 3; i > 0; i -= 3)
        {
            text2.Append(string.Join("---", ls.Skip(i).Take(3)));
            text2.Append("---");
        }

        return text2.ToString().Substring(0, text2.Length - 3);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("scala")).Equals(("a---c---s")));
    }

}
