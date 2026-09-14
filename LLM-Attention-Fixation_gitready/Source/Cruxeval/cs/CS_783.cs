using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text, string comparison) {
        int length = comparison.Length;
        if (length <= text.Length) {
            for (int i = 0; i < length; i++) {
                if (comparison[length - i - 1] != text[text.Length - i - 1]) {
                    return i;
                }
            }
        }
        return length;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("managed"), ("")) == (0L));
    }

}
