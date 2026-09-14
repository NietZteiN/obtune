using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> digits) {
        digits.Reverse();
        if (digits.Count < 2)
        {
            return digits;
        }
        for (int i = 0; i < digits.Count; i+=2)
        {
            long temp = digits[i];
            digits[i] = digits[i+1];
            digits[i+1] = temp;
        }
        return digits;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L}))).SequenceEqual((new List<long>(new long[]{(long)1L, (long)2L}))));
    }

}
