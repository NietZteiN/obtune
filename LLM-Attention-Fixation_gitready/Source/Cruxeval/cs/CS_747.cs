using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string text) {
        if (text == "42.42")
        {
            return true;
        }

        for (int i = 3; i < text.Length - 3; i++)
        {
            if (text[i] == '.' && text.Substring(i - 3).All(char.IsDigit) && text.Substring(0, i).All(char.IsDigit))
            {
                return true;
            }
        }

        return false;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("123E-10")) == (false));
    }

}
