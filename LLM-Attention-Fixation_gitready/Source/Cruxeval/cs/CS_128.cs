using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string odd = "";
        string even = "";
        for (int i = 0; i < text.Length; i++)
        {
            if (i % 2 == 0)
            {
                even += text[i];
            }
            else
            {
                odd += text[i];
            }
        }
        return even + odd.ToLower();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Mammoth")).Equals(("Mmohamt")));
    }

}
