import React from "react";
import { Sentiment } from "../../types";
import SentimentBlock from "./SentimentBlock";

interface Props {
  sentiment: Sentiment;
}

const SentimentCard = ({ sentiment }: Props) => (
  <div className="bg-brand-card border border-brand-border rounded-card p-8">
    <p className="text-md font-semibold text-brand-text mb-4">Sentiment</p>
    <div className="flex flex-col gap-4">
      <SentimentBlock label="Prepared statements" data={sentiment.prepared_statements} />
      <div className="border-t border-brand-border" />
      <SentimentBlock label="Q&A" data={sentiment.qa} />
    </div>
  </div>
);

export default SentimentCard;