using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string text) {
        if (text == "")
        {
            return false;
        }

        char firstChar = text[0];
        if (char.IsDigit(firstChar))
        {
            return false;
        }

        foreach (char lastChar in text)
        {
            if ((lastChar != '_') && !char.IsLetterOrDigit(lastChar))
            {
                return false;
            }
        }

        return true;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("meet")) == (true));
    }

}
