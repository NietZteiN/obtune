using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        int k = 0;
        int l = text.Length - 1;
        while (!char.IsLetter(text[l]))
        {
            l--;
        }
        while (!char.IsLetter(text[k]))
        {
            k++;
        }
        if (k != 0 || l != text.Length - 1)
        {
            return text.Substring(k, l - k + 1);
        }
        else
        {
            return text[0].ToString();
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("timetable, 2mil")).Equals(("t")));
    }

}
