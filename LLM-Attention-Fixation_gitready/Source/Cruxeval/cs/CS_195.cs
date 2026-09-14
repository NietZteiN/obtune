using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;

class Problem {
    public static string F(string text) {
        foreach (var p in new List<string> { "acs", "asp", "scn" })
        {
            if (text.StartsWith(p))
            {
                text = text.Substring(p.Length);
            }
            text += " ";
        }
        if (text.StartsWith(" "))
        {
            text = text.Substring(1);
        }
        return text.Substring(0, text.Length - 1);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ilfdoirwirmtoibsac")).Equals(("ilfdoirwirmtoibsac  ")));
    }

}
