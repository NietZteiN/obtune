using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string sentences) {
        string[] splitSentences = sentences.Split('.');
        if (splitSentences.All(sentence => long.TryParse(sentence, out _)))
        {
            return "oscillating";
        }
        else
        {
            return "not oscillating";
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("not numbers")).Equals(("not oscillating")));
    }

}
