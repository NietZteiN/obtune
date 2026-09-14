using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(string text, long chunks) {
        return text.Split(new string[] { "\n" }, StringSplitOptions.None).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("/alcm@ an)t//eprw)/e!/d\nujv"), (0L)).SequenceEqual((new List<string>(new string[]{(string)"/alcm@ an)t//eprw)/e!/d", (string)"ujv"}))));
    }

}
