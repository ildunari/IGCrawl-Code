import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogClose,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { AlertCircle } from "lucide-react"

interface CancelScrapeDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onCancel: (savePartial: boolean) => void
  scraped: {
    followers: number
    following: number
  }
}

export function CancelScrapeDialog({
  open,
  onOpenChange,
  onCancel,
  scraped,
}: CancelScrapeDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]" aria-describedby="cancel-dialog-description">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-yellow-600" />
            Cancel Scrape
          </DialogTitle>
          <DialogDescription id="cancel-dialog-description">
            The scrape is in progress. What would you like to do with the data collected so far?
          </DialogDescription>
        </DialogHeader>
        <div className="py-4 space-y-3">
          <div className="text-sm text-muted-foreground">
            <div>Followers scraped: <span className="font-medium text-foreground">{scraped.followers}</span></div>
            <div>Following scraped: <span className="font-medium text-foreground">{scraped.following}</span></div>
          </div>
          <p className="text-sm text-muted-foreground">
            You can save the partial results or discard them completely.
          </p>
        </div>
        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            variant="destructive"
            onClick={() => onCancel(false)}
          >
            Discard Data
          </Button>
          <Button
            variant="default"
            onClick={() => onCancel(true)}
          >
            Save Partial Results
          </Button>
          <DialogClose asChild>
            <Button variant="outline">
              Continue Scraping
            </Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}