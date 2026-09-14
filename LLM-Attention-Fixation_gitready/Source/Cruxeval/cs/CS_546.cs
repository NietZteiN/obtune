using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string speaker) {
        while (text.StartsWith(speaker))
        {
            text = text.Substring(speaker.Length);
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("[CHARRUNNERS]Do you know who the other was? [NEGMENDS]"), ("[CHARRUNNERS]")).Equals(("Do you know who the other was? [NEGMENDS]")));
    }

}
