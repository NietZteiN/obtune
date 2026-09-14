using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        if (text.Contains(','))
        {
            var parts = text.Split(new char[] { ',' }, 2);
            return parts[1] + " " + parts[0];
        }
        return "," + text.Split(' ').Last() + " 0";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("244, 105, -90")).Equals((" 105, -90 244")));
    }

}
