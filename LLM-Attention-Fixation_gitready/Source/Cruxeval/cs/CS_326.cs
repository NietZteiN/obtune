using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        int number = 0;
        foreach (char t in text) {
            if (char.IsDigit(t)) {
                number += 1;
            }
        }
        return number;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Thisisastring")) == (0L));
    }

}
