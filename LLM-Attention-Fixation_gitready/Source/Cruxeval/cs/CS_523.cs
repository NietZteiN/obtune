using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;

class Problem {
    public static string F(string text) {
        char[] textArray = text.ToCharArray();
        for (int i = textArray.Length - 1; i >= 0; i--) {
            if (char.IsWhiteSpace(textArray[i])) {
                textArray[i] = '\u00A0'; // Unicode for non-breaking space
            }
        }
        return new string(textArray).Replace("\u00A0", "&nbsp;");
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("   ")).Equals(("&nbsp;&nbsp;&nbsp;")));
    }

}
