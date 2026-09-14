using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long position, string value) {
        int length = text.Length;
        int index = (int)(position % length);
        if (position < 0) {
            index = length / 2;
        }
        List<char> newText = text.ToList();
        newText.Insert(index, value[0]);
        newText.RemoveAt(length - 1);
        return new string(newText.ToArray());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("sduyai"), (1L), ("y")).Equals(("syduyi")));
    }

}
