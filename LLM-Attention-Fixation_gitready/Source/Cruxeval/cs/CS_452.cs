using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        int counter = 0;
        foreach (char c in text)
        {
            if (char.IsLetter(c))
            {
                counter++;
            }
        }
        return counter;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("l000*")) == (1L));
    }

}
