using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string prefix) {
        if(text.StartsWith(prefix))
        {
            text = text.Substring(prefix.Length);
        }
        text = text.First().ToString().ToUpper() + text.Substring(1);
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("qdhstudentamxupuihbuztn"), ("jdm")).Equals(("Qdhstudentamxupuihbuztn")));
    }

}
