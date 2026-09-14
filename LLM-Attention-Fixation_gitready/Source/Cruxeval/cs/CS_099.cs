using System;
using System.Diagnostics;

class Problem {
    public static string F(string text, string sep, long num) {
        int count = 0;
        int sepIndex = text.LastIndexOf(sep);
        while (sepIndex != -1 && count < num) {
            text = text.Remove(sepIndex, sep.Length).Insert(sepIndex, "___");
            count++;
            sepIndex = text.LastIndexOf(sep);
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("aa+++bb"), ("+"), (1L)).Equals(("aa++___bb")));
    }

}
