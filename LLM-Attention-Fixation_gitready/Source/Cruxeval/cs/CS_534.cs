using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string sequence, string value) {
        int i = Math.Max(sequence.IndexOf(value) - sequence.Length / 3, 0);
        string result = "";
        for (int j = 0; j < sequence.Substring(i).Length; j++)
        {
            if (sequence[i + j] == '+')
            {
                result += value;
            }
            else
            {
                result += sequence[i + j];
            }
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("hosu"), ("o")).Equals(("hosu")));
    }

}
