using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string text) {
        bool b = true;
        foreach (char x in text)
        {
            if (char.IsDigit(x))
            {
                b = true;
            }
            else
            {
                b = false;
                break;
            }
        }
        return b;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("-1-3")) == (false));
    }

}
