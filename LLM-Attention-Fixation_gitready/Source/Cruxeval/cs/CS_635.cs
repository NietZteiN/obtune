using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string text) {
        char[] validChars = { '-', '_', '+', '.', '/', ' ' };
        text = text.ToUpper();
        foreach (char c in text)
        {
            if (!char.IsLetterOrDigit(c) && !validChars.Contains(c))
            {
                return false;
            }
        }
        return true;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("9.twCpTf.H7 HPeaQ^ C7I6U,C:YtW")) == (false));
    }

}
