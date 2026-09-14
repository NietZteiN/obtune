using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(List<string> numbers, long num, long val) {
        while (numbers.Count < num)
        {
            numbers.Insert(numbers.Count / 2, val.ToString());
        }
        for (long _ = 0; _ < numbers.Count / (num - 1) - 4; _++)
        {
            numbers.Insert(numbers.Count / 2, val.ToString());
        }
        return string.Join(" ", numbers);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>()), (0L), (1L)).Equals(("")));
    }

}
