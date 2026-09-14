using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string cat) {
        int digits = 0;
        foreach (char c in cat) {
            if (char.IsDigit(c)) {
                digits++;
            }
        }
        return digits;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("C24Bxxx982ab")) == (5L));
    }

}
