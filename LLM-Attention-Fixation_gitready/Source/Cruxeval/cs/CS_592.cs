using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> numbers) {
        List<long> new_numbers = new List<long>();
        for (int i = 0; i < numbers.Count; i++)
        {
            new_numbers.Add(numbers[numbers.Count - 1 - i]);
        }
        return new_numbers;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)11L, (long)3L}))).SequenceEqual((new List<long>(new long[]{(long)3L, (long)11L}))));
    }

}
