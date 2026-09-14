using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        StringBuilder ans = new StringBuilder();
        foreach (char c in text)
        {
            if (char.IsDigit(c))
            {
                ans.Append(c);
            }
            else
            {
                ans.Append(' ');
            }
        }
        return ans.ToString();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("m4n2o")).Equals((" 4 2 ")));
    }

}
