using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string forest, string animal) {
        int index = forest.IndexOf(animal);
        char[] result = forest.ToCharArray();
        while (index < forest.Length - 1)
        {
            result[index] = forest[index + 1];
            index++;
        }
        if (index == forest.Length - 1)
        {
            result[index] = '-';
        }
        return new string(result);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("2imo 12 tfiqr."), ("m")).Equals(("2io 12 tfiqr.-")));
    }

}
