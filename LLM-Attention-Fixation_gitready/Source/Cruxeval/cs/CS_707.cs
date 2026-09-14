using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long position) {
        int length = text.Length;
        int index = (int)(position % (length + 1));
        if (position < 0 || index < 0) {
            index = -1;
        }
        List<char> newText = text.ToList();
        newText.RemoveAt(index);
        return string.Join("", newText);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("undbs l"), (1L)).Equals(("udbs l")));
    }

}
