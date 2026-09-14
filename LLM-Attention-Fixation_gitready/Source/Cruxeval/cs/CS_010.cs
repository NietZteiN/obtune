using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string new_text = "";
        foreach (char ch in text.ToLower().Trim()) {
            if (char.IsDigit(ch) || ch == 'Ä' || ch == 'ä' || ch == 'Ï' || ch == 'ï' || ch == 'Ö' || ch == 'ö' || ch == 'Ü' || ch == 'ü') {
                new_text += ch;
            }
        }
        return new_text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("")).Equals(("")));
    }

}
