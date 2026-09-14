using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string text) {
        for (int i = 1; i < text.Length; i++)
        {
            if (text[i] == char.ToUpper(text[i]) && char.IsLower(text[i - 1]))
            {
                return true;
            }
        }
        return false;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("jh54kkk6")) == (true));
    }

}
