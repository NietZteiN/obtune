using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string chars) {
        if (!string.IsNullOrEmpty(chars))
        {
            text = text.TrimEnd(chars.ToCharArray());
        }
        else
        {
            text = text.TrimEnd();
        }
        if (text == "")
        {
            return "-";
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("new-medium-performing-application - XQuery 2.2"), ("0123456789-")).Equals(("new-medium-performing-application - XQuery 2.")));
    }

}
