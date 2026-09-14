using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string letters = "";
        foreach (char c in text)
        {
            if (char.IsLetterOrDigit(c))
            {
                letters += c;
            }
        }
        return letters;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("we@32r71g72ug94=(823658*!@324")).Equals(("we32r71g72ug94823658324")));
    }

}
