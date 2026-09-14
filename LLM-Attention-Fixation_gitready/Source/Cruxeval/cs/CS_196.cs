using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
using System.Globalization;

class Problem {
    public static string F(string text) {
        text = text.Replace(" x", " x.");
        if (CultureInfo.CurrentCulture.TextInfo.ToTitleCase(text) == text)
        {
            return "correct";
        }
        text = text.Replace(" x.", " x");
        return "mixed";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("398 Is A Poor Year To Sow")).Equals(("correct")));
    }

}
