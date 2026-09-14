using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(List<long> nums) {
        var score = new Dictionary<int, string> {
            {0, "F"},
            {1, "E"},
            {2, "D"},
            {3, "C"},
            {4, "B"},
            {5, "A"},
            {6, ""}
        };

        var result = new List<string>();
        foreach (var num in nums) {
            result.Add(score.ContainsKey((int)num) ? score[(int)num] : "");
        }

        return string.Join("", result);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)4L, (long)5L}))).Equals(("BA")));
    }

}
